import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MapPin, Plus, Edit2, Trash2, Building2, Home, Users } from 'lucide-react'
import { API_CONFIG, API_ENDPOINTS } from '../config/api'
import LocationModal from '../components/modals/LocationModal'
import { Location } from '../types'
import { usePermissions } from '../hooks/usePermissions'
import PermissionGuard from '../components/PermissionGuard'

export default function Locations() {
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedLocation, setSelectedLocation] = useState<Location | undefined>()
  const { isAdmin, isDirector } = usePermissions()

  const { data: locations, isLoading } = useQuery({
    queryKey: ['locations', API_CONFIG.DEFAULT_TENANT_ID],
    queryFn: async () => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.LOCATIONS}?tenant_id=${API_CONFIG.DEFAULT_TENANT_ID}`)
      if (!response.ok) throw new Error('Failed to fetch locations')
      return response.json() as Promise<Location[]>
    }
  })

  const createMutation = useMutation({
    mutationFn: async (locationData: Partial<Location>) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.LOCATIONS}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(locationData)
      })
      if (!response.ok) throw new Error('Failed to create location')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
      setIsModalOpen(false)
      setSelectedLocation(undefined)
    }
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Location> }) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.LOCATIONS}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to update location')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
      setIsModalOpen(false)
      setSelectedLocation(undefined)
    }
  })

  const deleteMutation = useMutation({
    mutationFn: async (locationId: string) => {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.LOCATIONS}/${locationId}`, {
        method: 'DELETE'
      })
      if (!response.ok) throw new Error('Failed to delete location')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
    }
  })

  const handleCreate = () => {
    setSelectedLocation(undefined)
    setIsModalOpen(true)
  }

  const handleEdit = (location: Location) => {
    setSelectedLocation(location)
    setIsModalOpen(true)
  }

  const handleDelete = async (locationId: string) => {
    if (window.confirm('确定要删除这个位置吗？')) {
      deleteMutation.mutate(locationId)
    }
  }

  const handleSave = (locationData: Partial<Location>) => {
    if (selectedLocation) {
      updateMutation.mutate({ id: selectedLocation.location_id, data: locationData })
    } else {
      createMutation.mutate(locationData)
    }
  }

  const getLocationTypeIcon = (type: string) => {
    return type === 'HomeCare' ? Home : Building2
  }

  const getLocationTypeBadge = (type: string) => {
    return type === 'HomeCare' 
      ? 'bg-green-100 text-green-800' 
      : 'bg-blue-100 text-blue-800'
  }

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  const institutionalLocations = locations?.filter(l => l.location_type === 'Institutional') || []
  const homeCareLocations = locations?.filter(l => l.location_type === 'HomeCare') || []
  const publicSpaces = locations?.filter(l => l.is_public_space) || []

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <MapPin className="w-8 h-8" />
            位置管理
          </h1>
          <p className="text-gray-600 mt-2">管理机构房间和居家护理位置</p>
        </div>
        <PermissionGuard requires={(p) => p.isAdmin || p.isDirector}>
          <button onClick={handleCreate} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            <Plus className="w-5 h-5" />
            添加位置
          </button>
        </PermissionGuard>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-gray-900">{locations?.length || 0}</div>
          <div className="text-gray-600 text-sm mt-1">总位置数</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-blue-600">{institutionalLocations.length}</div>
          <div className="text-gray-600 text-sm mt-1">机构房间</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-green-600">{homeCareLocations.length}</div>
          <div className="text-gray-600 text-sm mt-1">居家护理</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="text-3xl font-bold text-purple-600">{publicSpaces.length}</div>
          <div className="text-gray-600 text-sm mt-1">公共空间</div>
        </div>
      </div>

      {/* Locations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {locations?.map((location) => {
          const Icon = getLocationTypeIcon(location.location_type)
          return (
            <div key={location.location_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-lg ${location.location_type === 'HomeCare' ? 'bg-green-100' : 'bg-blue-100'}`}>
                    <Icon className={`w-6 h-6 ${location.location_type === 'HomeCare' ? 'text-green-600' : 'text-blue-600'}`} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{location.location_name}</h3>
                    <p className="text-sm text-gray-500">{location.location_tag || location.door_number}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <PermissionGuard requires={(p) => p.isAdmin || p.isDirector}>
                    <button onClick={() => handleEdit(location)} className="p-2 text-gray-400 hover:text-blue-600 transition" title="编辑">
                      <Edit2 className="w-4 h-4" />
                    </button>
                  </PermissionGuard>
                  <PermissionGuard requires={(p) => p.isAdmin}>
                    <button onClick={() => handleDelete(location.location_id)} className="p-2 text-gray-400 hover:text-red-600 transition" title="删除">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </PermissionGuard>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">类型</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLocationTypeBadge(location.location_type)}`}>
                    {location.location_type === 'HomeCare' ? '居家护理' : '机构护理'}
                  </span>
                </div>

                {location.building && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">楼栋/楼层</span>
                    <span className="text-gray-900">
                      {location.building} {location.floor && `· ${location.floor}`}
                    </span>
                  </div>
                )}

                {location.area_id && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">区域</span>
                    <span className="text-gray-900">{location.area_id}</span>
                  </div>
                )}

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">门牌号</span>
                  <span className="text-gray-900">{location.door_number}</span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">时区</span>
                  <span className="text-gray-900">{location.timezone}</span>
                </div>

                {/* Space Type */}
                <div className="flex items-center gap-2 pt-2">
                  {location.is_public_space && (
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                      公共空间
                    </span>
                  )}
                  {location.is_multi_person_room && (
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full flex items-center gap-1">
                      <Users className="w-3 h-3" />
                      多人房间
                    </span>
                  )}
                  {location.is_active ? (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      监控中
                    </span>
                  ) : (
                    <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                      已禁用
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Empty State */}
      {locations?.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">暂无位置数据</p>
          <PermissionGuard requires={(p) => p.isAdmin || p.isDirector}>
            <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              创建第一个位置
            </button>
          </PermissionGuard>
        </div>
      )}

      {/* Location Modal */}
      <LocationModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedLocation(undefined)
        }}
        onSave={handleSave}
        location={selectedLocation}
        tenantId={API_CONFIG.DEFAULT_TENANT_ID}
      />
    </div>
  )
}
