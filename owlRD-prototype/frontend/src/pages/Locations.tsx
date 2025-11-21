import { useQuery } from '@tanstack/react-query'
import { MapPin, Building2, Home, Plus, Edit2, Trash2, Users } from 'lucide-react'

interface Location {
  location_id: string
  tenant_id: string
  location_tag?: string
  location_name: string
  building?: string
  floor?: string
  area_id?: string
  door_number: string
  location_type: string
  primary_resident_id?: string
  is_public_space: boolean
  is_multi_person_room: boolean
  timezone: string
  is_active: boolean
  created_at: string
  updated_at: string
}

const TENANT_ID = '10000000-0000-0000-0000-000000000001'

export default function Locations() {
  const { data: locations, isLoading } = useQuery({
    queryKey: ['locations', TENANT_ID],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/locations?tenant_id=${TENANT_ID}`)
      if (!response.ok) throw new Error('Failed to fetch locations')
      return response.json() as Promise<Location[]>
    }
  })

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
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          <Plus className="w-5 h-5" />
          添加位置
        </button>
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
                  <button className="p-2 text-gray-400 hover:text-blue-600 transition">
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600 transition">
                    <Trash2 className="w-4 h-4" />
                  </button>
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
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            创建第一个位置
          </button>
        </div>
      )}
    </div>
  )
}
